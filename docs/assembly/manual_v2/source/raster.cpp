#include <cmath>
#include <algorithm>
extern "C" void raster(int w,int h,int n,const double* t,const unsigned char* col,unsigned char* img,double* depth){
 for(int i=0;i<n;i++){
 const double *a=t+9*i,*b=a+3,*c=b+3; double den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(fabs(den)<1e-8)continue;
 int x0=std::max(0,(int)floor(std::min({a[0],b[0],c[0]}))),x1=std::min(w-1,(int)ceil(std::max({a[0],b[0],c[0]})));
 int y0=std::max(0,(int)floor(std::min({a[1],b[1],c[1]}))),y1=std::min(h-1,(int)ceil(std::max({a[1],b[1],c[1]})));
 for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
 double u=((b[1]-c[1])*(x+.5-c[0])+(c[0]-b[0])*(y+.5-c[1]))/den;
 double v=((c[1]-a[1])*(x+.5-c[0])+(a[0]-c[0])*(y+.5-c[1]))/den;double q=1-u-v;
 if(u<0||v<0||q<0)continue;double z=u*a[2]+v*b[2]+q*c[2];int p=y*w+x;if(z>depth[p]){depth[p]=z;for(int j=0;j<3;j++)img[p*3+j]=col[i*3+j];}
 }
 }
}
